
public class DatabaseConnection {
  private static 
<<<<<<< ./senarios_merge_base/JDime/scenario_36/left/databaseConnection.java
  DatabaseConnection
=======
  String
>>>>>>> ./senarios_merge_base/JDime/scenario_36/right/databaseConnection.java
   
<<<<<<< ./senarios_merge_base/JDime/scenario_36/left/databaseConnection.java
  instance
=======
  connectionPool
>>>>>>> ./senarios_merge_base/JDime/scenario_36/right/databaseConnection.java
  ;

  private String url;

  private String driver;

  private DatabaseConnection(String url, String driver) {
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