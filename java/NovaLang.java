import java.util.ArrayList;
import java.util.List;

/** A dependency-free Java reference lexer for NovaLang source files. */
public final class NovaLang {
    record Token(String kind, String value, int line, int column) {}

    static List<Token> lex(String source) {
        List<Token> tokens = new ArrayList<>();
        int line = 1, column = 1;
        for (int i = 0; i < source.length();) {
            char current = source.charAt(i);
            if (current == ' ' || current == '\t' || current == '\r') { i++; column++; continue; }
            if (current == '\n') { i++; line++; column = 1; continue; }
            if (current == '/' && i + 1 < source.length() && source.charAt(i + 1) == '/') {
                while (i < source.length() && source.charAt(i) != '\n') { i++; column++; }
                continue;
            }
            int startColumn = column;
            if (Character.isDigit(current)) {
                int start = i;
                while (i < source.length() && (Character.isDigit(source.charAt(i)) || source.charAt(i) == '.')) { i++; column++; }
                tokens.add(new Token("number", source.substring(start, i), line, startColumn));
                continue;
            }
            if (Character.isLetter(current) || current == '_') {
                int start = i;
                while (i < source.length() && (Character.isLetterOrDigit(source.charAt(i)) || source.charAt(i) == '_')) { i++; column++; }
                tokens.add(new Token("identifier", source.substring(start, i), line, startColumn));
                continue;
            }
            if (current == '"') {
                int start = ++i; column++;
                while (i < source.length() && source.charAt(i) != '"') { i++; column++; }
                if (i == source.length()) throw new IllegalArgumentException("Unclosed string at " + line + ":" + startColumn);
                tokens.add(new Token("string", source.substring(start, i), line, startColumn));
                i++; column++; continue;
            }
            String two = i + 1 < source.length() ? source.substring(i, i + 2) : "";
            if (two.equals("==") || two.equals("!=") || two.equals("<=") || two.equals(">=") || two.equals("&&") || two.equals("||")) {
                tokens.add(new Token("operator", two, line, startColumn)); i += 2; column += 2; continue;
            }
            tokens.add(new Token("symbol", String.valueOf(current), line, startColumn)); i++; column++;
        }
        tokens.add(new Token("EOF", "", line, column));
        return tokens;
    }

    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: java NovaLang <source.nova>");
            return;
        }
        try {
            String source = java.nio.file.Files.readString(java.nio.file.Path.of(args[0]));
            lex(source).forEach(token -> System.out.printf("%-10s %-12s %d:%d%n", token.kind(), token.value(), token.line(), token.column()));
        } catch (java.io.IOException error) {
            System.err.println("Could not read source: " + error.getMessage());
            System.exit(1);
        }
    }
}
