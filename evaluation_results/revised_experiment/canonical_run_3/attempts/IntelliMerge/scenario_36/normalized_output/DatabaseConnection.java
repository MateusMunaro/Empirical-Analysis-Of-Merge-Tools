public class DatabaseConnection {
    private static DatabaseConnection instance;
    private String url;
    private String driver;
    private String connectionPool;
    
    // Public constructor for factory access
<<<<<<< ours
    private DatabaseConnection(String url)
=======
    public DatabaseConnection(String url, String driver)
>>>>>>> theirs
     {
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
    
    public static void resetInstance() {
        instance = null;
    }
    public void setConnectionPool(String pool) {
        this.connectionPool = pool;
    }
}
