public class DatabaseConnection {
    private String url;
    private String driver;
    
    public DatabaseConnection(String url) {
        this.url = url;
        this.driver = "default";
    }
    
    public void connect() {
        System.out.println("Connecting to: " + url);
    }
}