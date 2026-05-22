public class DatabaseConnectionFactory {
    public static DatabaseConnection createConnection(String type, String url) {
        String driver;
        switch(type) {
            case "mysql":
                driver = "com.mysql.cj.jdbc.Driver";
                return new DatabaseConnection("mysql://" + url, driver);
            case "postgres":
                driver = "org.postgresql.Driver";
                return new DatabaseConnection("postgresql://" + url, driver);
            case "oracle":
                driver = "oracle.jdbc.driver.OracleDriver";
                return new DatabaseConnection("oracle:thin:@" + url, driver);
            default:
                throw new IllegalArgumentException("Unknown database type: " + type);
        }
    }
    
    public static DatabaseConnection createDefaultConnection(String url) {
        return new DatabaseConnection(url, "default-driver");
    }
}