
public class DatabaseConnection {
  private static 
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_36/left/DatabaseConnection.java
  DatabaseConnection
=======
  String
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_36/right/DatabaseConnection.java
   
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_36/left/DatabaseConnection.java
  instance
=======
  connectionPool
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_36/right/DatabaseConnection.java
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