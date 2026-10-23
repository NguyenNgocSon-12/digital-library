package vn.edu.huit.digitallibrary.reading.dto;

import tools.jackson.core.JsonParser;
import tools.jackson.core.JsonToken;
import tools.jackson.databind.DeserializationContext;
import tools.jackson.databind.ValueDeserializer;

/** Keep strict integer validation local to progress; do not alter the shared JSON mapper. */
public class ProgressIntegerDeserializer extends ValueDeserializer<Integer> {
    @Override
    public Integer deserialize(JsonParser parser, DeserializationContext context) {
        if (parser.currentToken() != JsonToken.VALUE_NUMBER_INT) {
            return context.reportInputMismatch(Integer.class, "Vị trí đọc phải là số nguyên JSON");
        }
        return parser.getIntValue();
    }
}
