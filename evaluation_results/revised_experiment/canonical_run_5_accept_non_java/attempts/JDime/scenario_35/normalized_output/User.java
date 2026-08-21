
public class User {
  private String username;

  private int age;

  public void setAge(int age) {

<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_35/left/User.java
    if (age < 0) {
      throw new IllegalArgumentException("Age cannot be negative");
    }
=======
    if (age < 18 || age > 150) {
      throw new IllegalArgumentException("Age must be between 18 and 150");
    }
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_35/right/User.java

    this.age = age;
  }
}