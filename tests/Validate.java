// Minimal XSD 1.0 validator using the JDK's built-in (Xerces-based) javax.xml.validation.
// Usage: java Validate.java <schema.xsd> <file1.xml> [file2.xml ...]
// Prints one line per file: "OK<TAB>path" or "ERR<TAB>path<TAB>message".
import javax.xml.XMLConstants;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.*;
import java.io.File;

public class Validate {
    public static void main(String[] a) throws Exception {
        SchemaFactory f = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);
        Schema s = f.newSchema(new File(a[0]));
        for (int i = 1; i < a.length; i++) {
            Validator v = s.newValidator();
            try { v.validate(new StreamSource(new File(a[i]))); System.out.println("OK\t" + a[i]); }
            catch (Exception e) { System.out.println("ERR\t" + a[i] + "\t" + String.valueOf(e.getMessage()).replace('\n', ' ')); }
        }
    }
}
