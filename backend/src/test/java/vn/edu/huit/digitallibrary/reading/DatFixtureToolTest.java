package vn.edu.huit.digitallibrary.reading;

import static com.mongodb.client.model.Filters.eq;
import static com.mongodb.client.model.Projections.excludeId;
import static com.mongodb.client.model.Projections.fields;
import static com.mongodb.client.model.Projections.include;
import static org.assertj.core.api.Assertions.assertThat;

import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.ReplaceOptions;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.bson.Document;
import org.bson.types.ObjectId;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;
import org.springframework.data.redis.connection.RedisPassword;
import org.springframework.data.redis.connection.RedisStandaloneConfiguration;
import org.springframework.data.redis.connection.lettuce.LettuceConnectionFactory;
import org.springframework.data.redis.core.ScanOptions;
import org.springframework.data.redis.core.RedisCallback;
import java.util.Properties;
import org.springframework.data.redis.core.StringRedisTemplate;

/** Standalone opt-in tool, independent of Spring application and the production API. */
@EnabledIfEnvironmentVariable(named = "DAT_FIXTURE_ACTION", matches = "seed|benchmark|verify")
class DatFixtureToolTest {
    private static final String OWNER = "dat-fixture-tool-v1";
    private final String namespace = env("DAT_FIXTURE_NAMESPACE", "dat-fixture:v1:");
    private final String database = env("DAT_FIXTURE_DATABASE", "digital_library_dat_fixture_v1");
    private final Path output = Path.of(env("DAT_FIXTURE_OUTPUT", "../docs/dat/evidence/fixture")).toAbsolutePath().normalize();
    private final ReplaceOptions upsert = new ReplaceOptions().upsert(true);

    @Test
    void runTool() throws Exception {
        require(namespace.matches("dat-fixture:[a-z0-9-]+:"), "Namespace must be dat-fixture:<name>:");
        require(database.matches("digital_library_dat_fixture_[a-z0-9_]+"), "Dedicated fixture Mongo database required");
        URI redisUri = URI.create(env("DAT_FIXTURE_REDIS_URL", "redis://localhost:6379/0"));
        require("redis".equals(redisUri.getScheme()), "Use redis:// for this local fixture tool");
        RedisStandaloneConfiguration config = new RedisStandaloneConfiguration(redisUri.getHost(),
                redisUri.getPort() < 0 ? 6379 : redisUri.getPort());
        if (redisUri.getPath() != null && redisUri.getPath().length() > 1) {
            config.setDatabase(Integer.parseInt(redisUri.getPath().substring(1)));
        }
        if (redisUri.getUserInfo() != null) {
            String[] auth = redisUri.getUserInfo().split(":", 2);
            if (!auth[0].isEmpty()) config.setUsername(auth[0]);
            if (auth.length == 2) config.setPassword(RedisPassword.of(auth[1]));
        }
        var factory = new LettuceConnectionFactory(config);
        factory.afterPropertiesSet();
        factory.start();
        var redis = new StringRedisTemplate(factory);
        try (MongoClient mongo = MongoClients.create(env("DAT_FIXTURE_MONGO_URI",
                "mongodb://admin:admin123@localhost:27017/?authSource=admin"))) {
            MongoDatabase db = mongo.getDatabase(database);
            Files.createDirectories(output);
            if ("seed".equals(System.getenv("DAT_FIXTURE_ACTION"))) {
                claimMongo(db);
                claimRedis(redis);
                Document manifest = loadOrCreateManifest(mongo, db);
                validateManifest(mongo, manifest);
                seed(db, redis, manifest);
                var before = snapshot(redis, manifest);
                String sentinelKey = namespace + "preserve-check";
                redis.opsForValue().setIfAbsent(sentinelKey, "preserve fixture sentinel");
                String sentinel = redis.opsForValue().get(sentinelKey);
                Document first = manifest.getList("entries", Document.class).get(0);
                redis.opsForHash().put(progressKey(first), "page", "999");
                redis.opsForZSet().incrementScore(namespace + "ranking:books", first.getString("bookId"), 77);
                // Rerun exactly the owned fixture to verify deterministic reset and preservation.
                seed(db, redis, manifest);
                assertThat(snapshot(redis, manifest)).isEqualTo(before);
                assertThat(redis.opsForValue().get(sentinelKey)).isEqualTo(sentinel);
                Files.writeString(output.resolve("manifest.json"), manifest.toJson(), StandardCharsets.UTF_8);
                Document verification = new Document("time", Instant.now().toString())
                        .append("database", database).append("namespace", namespace)
                        .append("progressHashes", manifest.getList("entries", Document.class).size())
                        .append("rankingMembers", redis.opsForZSet().zCard(namespace + "ranking:books"))
                        .append("rerunIdentical", true).append("mutatedFixtureReset", true)
                        .append("unregisteredSentinelPreserved", true).append("sourceDatabase", manifest.getString("sourceDatabase"));
                Files.writeString(output.resolve("seed-verification.json"), verification.toJson());
                System.out.println("DAT_FIXTURE " + verification.toJson());
            } else {
                require(OWNER.equals(redis.opsForValue().get(namespace + "owner")), "Fixture Redis owner missing");
                Document marker = db.getCollection("fixture_metadata").find(eq("_id", "owner")).first();
                require(marker != null && OWNER.equals(marker.getString("owner")), "Fixture Mongo owner missing or wrong");
                Document manifest = Document.parse(Files.readString(output.resolve("manifest.json")));
                require(database.equals(manifest.getString("fixtureDatabase")) && namespace.equals(manifest.getString("namespace")),
                        "Manifest does not match the selected fixture");
                if ("verify".equals(System.getenv("DAT_FIXTURE_ACTION"))) {
                    validateManifest(mongo, manifest);
                    List<Document> rows = new ArrayList<>();
                    for (Document e : manifest.getList("entries", Document.class)) {
                        String key = progressKey(e);
                        assertThat(redis.type(key).code()).isEqualTo("hash");
                        assertThat(readRedis(redis, e)).isEqualTo(progressValue(e));
                        assertThat(redis.getExpire(key)).isEqualTo(-1L);
                        assertThat(redis.opsForZSet().score(namespace + "ranking:books", e.getString("bookId")))
                                .isEqualTo(e.getInteger("score").doubleValue());
                        assertThat(readMongo(db, e)).containsExactlyInAnyOrderEntriesOf(readRedis(redis, e));
                        rows.add(new Document("key", key).append("mongoReferenceValid", true)
                                .append("fields", new Document(readRedis(redis, e)))
                                .append("type", redis.type(key).code()).append("hlen", redis.opsForHash().size(key))
                                .append("ttl", redis.getExpire(key)).append("score", e.getInteger("score")));
                    }
                    long hashCount = 0;
                    try (var keys = redis.scan(ScanOptions.scanOptions().match(namespace + "progress:*").count(100).build())) {
                        while (keys.hasNext()) { keys.next(); hashCount++; }
                    }
                    assertThat(hashCount).isEqualTo(rows.size());
                    assertThat(redis.opsForZSet().zCard(namespace + "ranking:books")).isEqualTo(50L);
                    Document audit = new Document("time", Instant.now().toString()).append("readOnly", true)
                            .append("hashCount", hashCount).append("zcard", 50).append("rows", rows);
                    Files.writeString(output.resolve("fixture-audit.json"), audit.toJson());
                    System.out.println("DAT_FIXTURE_AUDIT hashCount=" + hashCount + " zcard=50 allReferencesValid=true");
                } else {
                    benchmark(db, redis, manifest, mongo, config);
                }
            }
        } finally {
            factory.destroy();
        }
    }

    private void claimMongo(MongoDatabase db) {
        Document marker = db.getCollection("fixture_metadata").find(eq("_id", "owner")).first();
        if (marker == null) {
            require(db.listCollectionNames().into(new ArrayList<>()).isEmpty(),
                    "Refusing existing Mongo database without ownership marker");
            db.getCollection("fixture_metadata").insertOne(new Document("_id", "owner").append("owner", OWNER));
        } else {
            require(OWNER.equals(marker.getString("owner")), "Different Mongo fixture owner");
        }
    }

    private void claimRedis(StringRedisTemplate redis) {
        String marker = redis.opsForValue().get(namespace + "owner");
        if (marker == null) {
            try (var keys = redis.scan(ScanOptions.scanOptions().match(namespace + "*").count(100).build())) {
                require(!keys.hasNext(), "Refusing existing Redis namespace without ownership marker");
            }
            require(Boolean.TRUE.equals(redis.opsForValue().setIfAbsent(namespace + "owner", OWNER)),
                    "Another seed claimed namespace concurrently");
        } else {
            require(OWNER.equals(marker), "Different Redis fixture owner");
        }
    }

    private Document loadOrCreateManifest(MongoClient mongo, MongoDatabase db) throws Exception {
        String input = System.getenv("DAT_FIXTURE_MANIFEST");
        if (input != null && !input.isBlank()) {
            Document manifest = Document.parse(Files.readString(Path.of(input)));
            // External source is READ ONLY; seed() writes only the owned fixture baseline/Redis namespace.
            manifest.put("fixtureDatabase", database);
            manifest.put("namespace", namespace);
            return manifest;
        }
        String userId = "da7100000000000000000001";
        Date created = Date.from(Instant.parse("2026-10-22T00:00:00Z"));
        Document user = new Document("_id", new ObjectId(userId)).append("fixtureOwner", OWNER)
                .append("username", "dat.fixture.reader").append("email", "dat.fixture@example.test")
                .append("passwordHash", "fixture-only-no-login").append("role", "USER").append("createdAt", created);
        replaceOwned(db, "users", user);
        List<Document> entries = new ArrayList<>();
        for (int i = 1; i <= 50; i++) {
            String bookId = String.format("da70000000000000%08x", i);
            List<Document> chapters = new ArrayList<>();
            for (int chapter = 1; chapter <= 5; chapter++) {
                chapters.add(new Document("chapterNo", chapter).append("title", "Chapter " + chapter)
                        .append("content", "Independent Dat fixture content " + i + "/" + chapter).append("sections", List.of()));
            }
            replaceOwned(db, "books", new Document("_id", new ObjectId(bookId)).append("fixtureOwner", OWNER)
                    .append("title", "Dat fixture " + i).append("author", "Dat fixture tool")
                    .append("categories", List.of("Fixture")).append("chapters", chapters).append("createdAt", created));
            entries.add(new Document("userId", userId).append("bookId", bookId)
                    .append("chapter", i % 5 + 1).append("page", i + 1).append("line", i % 3).append("score", i));
        }
        return new Document("version", 1).append("owner", OWNER).append("sourceDatabase", database)
                .append("fixtureDatabase", database).append("namespace", namespace).append("entries", entries);
    }

    private void replaceOwned(MongoDatabase db, String collection, Document value) {
        Document existing = db.getCollection(collection).find(eq("_id", value.get("_id"))).first();
        require(existing == null || OWNER.equals(existing.getString("fixtureOwner")), "Refusing non-owned Mongo document");
        db.getCollection(collection).replaceOne(eq("_id", value.get("_id")), value, upsert);
    }

    private void validateManifest(MongoClient mongo, Document manifest) {
        String source = manifest.getString("sourceDatabase");
        require(source != null && !source.isBlank(), "sourceDatabase required");
        List<Document> entries = manifest.getList("entries", Document.class);
        require(entries != null && entries.size() >= 50, "At least 50 progress entries required");
        require(entries.stream().map(e -> e.getString("userId") + ":" + e.getString("bookId")).distinct().count() == entries.size(),
                "Duplicate progress pair");
        require(entries.stream().map(e -> e.getString("bookId")).distinct().count() == 50, "Exactly 50 distinct books required");
        MongoDatabase sourceDb = mongo.getDatabase(source);
        for (Document entry : entries) {
            String user = entry.getString("userId"), book = entry.getString("bookId");
            require(ObjectId.isValid(user) && ObjectId.isValid(book), "Invalid ObjectId in manifest");
            require(entry.getInteger("chapter") >= 1 && entry.getInteger("page") >= 1 && entry.getInteger("line") >= 0,
                    "Invalid progress position");
            require(entry.getInteger("score") >= 0, "Invalid ranking score");
            require(sourceDb.getCollection("users").find(eq("_id", new ObjectId(user))).first() != null, "User absent in source Mongo");
            Document actual = sourceDb.getCollection("books").find(eq("_id", new ObjectId(book))).first();
            require(actual != null && actual.getList("chapters", Document.class).stream()
                    .anyMatch(c -> ((Number) c.get("chapterNo")).intValue() == entry.getInteger("chapter")), "Chapter absent in source Mongo");
        }
    }

    private void seed(MongoDatabase db, StringRedisTemplate redis, Document manifest) {
        String registry = namespace + "owned-keys";
        var previous = redis.opsForSet().members(registry);
        if (previous != null) {
            for (String key : previous) require(key.startsWith(namespace + "progress:")
                    || key.equals(namespace + "ranking:books"), "Unsafe key in ownership registry");
            if (!previous.isEmpty()) redis.delete(previous);
        }
        redis.delete(registry);
        // Register before writing so interruption leaves recoverable ownership information.
        List<Document> entries = manifest.getList("entries", Document.class);
        List<String> keys = new ArrayList<>();
        keys.add(namespace + "ranking:books");
        for (Document e : entries) keys.add(progressKey(e));
        for (String key : keys) require(!Boolean.TRUE.equals(redis.hasKey(key)), "Unregistered existing fixture key; refusing overwrite");
        redis.opsForSet().add(registry, keys.toArray(String[]::new));
        for (Document entry : entries) {
            Map<String, String> value = progressValue(entry);
            redis.opsForHash().putAll(progressKey(entry), value);
            redis.opsForZSet().add(namespace + "ranking:books", entry.getString("bookId"), entry.getInteger("score"));
            Document baseline = new Document("_id", pair(entry)).append("fixtureOwner", OWNER);
            value.forEach(baseline::append);
            replaceOwned(db, "progress_baseline", baseline);
        }
        assertThat(redis.opsForZSet().zCard(namespace + "ranking:books")).isEqualTo(50L);
        for (Document entry : entries) {
            assertThat(redis.type(progressKey(entry)).code()).isEqualTo("hash");
            assertThat(redis.opsForHash().entries(progressKey(entry))).containsExactlyInAnyOrderEntriesOf(progressValue(entry));
            assertThat(redis.getExpire(progressKey(entry))).isEqualTo(-1L);
        }
    }

    private Map<String, Object> snapshot(StringRedisTemplate redis, Document manifest) {
        Map<String, Object> values = new LinkedHashMap<>();
        values.put("ranking", redis.opsForZSet().reverseRangeWithScores(namespace + "ranking:books", 0, -1));
        for (Document entry : manifest.getList("entries", Document.class)) {
            values.put(progressKey(entry), redis.opsForHash().entries(progressKey(entry)));
        }
        return values;
    }

    private void benchmark(MongoDatabase db, StringRedisTemplate redis, Document manifest,
            MongoClient client, RedisStandaloneConfiguration redisConfig) throws Exception {
        int warmup = Integer.parseInt(env("DAT_BENCH_WARMUP", "200"));
        int runs = Integer.parseInt(env("DAT_BENCH_RUNS", "1000"));
        require(warmup >= 0 && runs >= 1, "Invalid benchmark counts");
        List<Document> entries = manifest.getList("entries", Document.class);
        // Verify equivalent payload before timing. No writes inside the benchmark.
        for (Document e : entries) assertThat(readMongo(db, e)).containsExactlyInAnyOrderEntriesOf(readRedis(redis, e));
        List<Long> mongoSamples = new ArrayList<>(), redisSamples = new ArrayList<>();
        StringBuilder raw = new StringBuilder("iteration,backend,elapsed_ns\n");
        for (int i = -warmup; i < runs; i++) {
            Document entry = entries.get(Math.floorMod(i, entries.size()));
            // Alternate order to reduce first/second backend bias; concurrency is one for both.
            for (int j = 0; j < 2; j++) {
                boolean useRedis = Math.floorMod(i + j, 2) == 0;
                long start = System.nanoTime();
                Map<?, ?> result = useRedis ? readRedis(redis, entry) : readMongo(db, entry);
                long elapsed = System.nanoTime() - start;
                require(result.size() == 4, "Unexpected benchmark payload");
                if (i >= 0) {
                    (useRedis ? redisSamples : mongoSamples).add(elapsed);
                    raw.append(i).append(',').append(useRedis ? "redis" : "mongo").append(',').append(elapsed).append('\n');
                }
            }
        }
        Files.writeString(output.resolve("benchmark-raw.csv"), raw);
        Properties redisServer = redis.execute((RedisCallback<Properties>) c -> c.serverCommands().info("server"));
        Properties redisPersistence = redis.execute((RedisCallback<Properties>) c -> c.serverCommands().info("persistence"));
        Document summary = new Document("time", Instant.now().toString()).append("java", System.getProperty("java.version"))
                .append("os", System.getProperty("os.name") + " " + System.getProperty("os.arch"))
                .append("availableProcessors", Runtime.getRuntime().availableProcessors())
                .append("mongoVersion", db.runCommand(new Document("buildInfo", 1)).getString("version"))
                .append("redisVersion", redisServer.getProperty("redis_version"))
                .append("redisAofEnabled", redisPersistence.getProperty("aof_enabled"))
                .append("redisDatabase", redisConfig.getDatabase())
                .append("redisEndpoint", redisConfig.getHostName() + ":" + redisConfig.getPort())
                .append("mongoEndpoint", client.getClusterDescription().getServerDescriptions().stream().map(s -> s.getAddress().toString()).toList())
                .append("fixtureDatabase", database).append("namespace", namespace)
                .append("datasetSize", entries.size()).append("warmupPerBackend", warmup).append("runsPerBackend", runs)
                .append("concurrency", 1).append("order", "alternating paired reads, pooled persistent clients")
                .append("operation", "Redis HGETALL vs Mongo findOne indexed _id projecting identical four string fields; full result materialized")
                .append("quantile", "nearest rank ceil(p*N); elapsed_ns / 1e6 = ms")
                .append("errors", 0).append("mongo", stats(mongoSamples)).append("redis", stats(redisSamples));
        Files.writeString(output.resolve("benchmark-summary.json"), summary.toJson());
        System.out.println("DAT_BENCHMARK " + summary.toJson());
    }

    private Map<String, String> readRedis(StringRedisTemplate redis, Document entry) {
        return redis.<String, String>opsForHash().entries(progressKey(entry));
    }

    private Document readMongo(MongoDatabase db, Document entry) {
        return db.getCollection("progress_baseline").find(eq("_id", pair(entry)))
                .projection(fields(include("chapter", "page", "line", "updatedAt"), excludeId())).first();
    }

    private Document stats(List<Long> samples) {
        var sorted = samples.stream().sorted().toList();
        return new Document("count", sorted.size()).append("meanMs", sorted.stream().mapToLong(Long::longValue).average().orElseThrow() / 1e6)
                .append("medianMs", sorted.get((int) Math.ceil(sorted.size() * .5) - 1) / 1e6)
                .append("p95Ms", sorted.get((int) Math.ceil(sorted.size() * .95) - 1) / 1e6);
    }

    private Map<String, String> progressValue(Document entry) {
        return Map.of("chapter", entry.getInteger("chapter").toString(), "page", entry.getInteger("page").toString(),
                "line", entry.getInteger("line").toString(), "updatedAt", "2026-10-22T00:00:00Z");
    }

    private String pair(Document entry) { return entry.getString("userId") + ":" + entry.getString("bookId"); }
    private String progressKey(Document entry) { return namespace + "progress:" + pair(entry); }
    private static String env(String key, String fallback) {
        String value = System.getenv(key);
        return value == null || value.isBlank() ? fallback : value;
    }
    private static void require(boolean condition, String message) {
        if (!condition) throw new IllegalStateException(message);
    }
}
