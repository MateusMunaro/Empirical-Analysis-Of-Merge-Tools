public class DatabaseConnection {
    private static DatabaseConnection instance;
    private String url;
    private String driver;
    
    private DatabaseConnection(String url) {
        this.url = url;
        this.driver = "default";
    }
    
    public static DatabaseConnection getInstance(String url) {
        if (instance == null) {
            instance = new DatabaseConnection(url);
        }
        return instance;
    }
    
    public void connect() {
        System.out.println("Connecting to: " + url);
    }
    
    public static void resetInstance() {
        instance = null;
    }
}