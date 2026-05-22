public   class  DatabaseConnection {
	
    private String url  ;

	
    private String driver  ;

	
    
    public DatabaseConnection  (String url) {
        this.url = url;
        this.driver = "default";
    
        this.url = url;
        this.driver = "default";
    }

	
    
    public void connect  () {
        System.out.println("Connecting to: " + url + " using driver: " + driver);
    }

	
    private static DatabaseConnection instance;

	
    
    public static DatabaseConnection getInstance(String url) {
        if (instance == null) {
            instance = new DatabaseConnection(url);
        }
        return instance;
    }

	
    
    public static void resetInstance() {
        instance = null;
    }

	
    private String connectionPool;

	
    
    // Public constructor for factory access
    public DatabaseConnection(String url, String driver) {
        this.url = url;
        this.driver = driver;
        this.connectionPool = "default-pool";
    }

	
    
    public void setConnectionPool(String pool) {
        this.connectionPool = pool;
    }


}
