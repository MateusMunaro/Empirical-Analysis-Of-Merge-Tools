public class DatabaseConnection {
    private static DatabaseConnection instance;
    private String url;
    private String driver;
    private String connectionPool;
    
    // Constructor privado para singleton
    private DatabaseConnection(String url) {
        this.url = url;
        this.driver = "default";
        this.connectionPool = "default-pool";
    }
    
    // Constructor público para factory access
    public DatabaseConnection(String url, String driver) {
        this.url = url;
        this.driver = driver;
        this.connectionPool = "default-pool";
    }
    
    public static DatabaseConnection getInstance(String url) {
        if (instance == null) {
            instance = new DatabaseConnection(url);
        }
        return instance;
    }
    
    public void connect() {
        System.out.println("Connecting to: " + url + " using driver: " + driver);
    }
    
    public void setConnectionPool(String pool) {
        this.connectionPool = pool;
    }
    
    public static void resetInstance() {
        instance = null;
    }
}