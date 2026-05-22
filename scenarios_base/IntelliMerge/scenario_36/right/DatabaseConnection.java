public class DatabaseConnection {
    private String url;
    private String driver;
    private String connectionPool;
    
    // Public constructor for factory access
    public DatabaseConnection(String url, String driver) {
        this.url = url;
        this.driver = driver;
        this.connectionPool = "default-pool";
    }
    
    public void connect() {
        System.out.println("Connecting to: " + url + " using driver: " + driver);
    }
    
    public void setConnectionPool(String pool) {
        this.connectionPool = pool;
    }
}

