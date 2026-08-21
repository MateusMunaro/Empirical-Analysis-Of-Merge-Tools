
public class TeamManager {
  private 
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_37/left/TeamManager.java
  List
=======
  Set
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_37/right/TeamManager.java
  <String> members = new 
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_37/left/TeamManager.java
  ArrayList
=======
  HashSet
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_37/right/TeamManager.java
  <>();

  public void addMember(String member) {

<<<<<<< Unknown file: This is a bug in JDime.
=======
    if (members.contains(member)) {
      throw new IllegalArgumentException("Member already exists");
    }
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_37/right/TeamManager.java

    members.add(member);
  }

  public 
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_37/left/TeamManager.java
  List
=======
  Set
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_37/right/TeamManager.java
  <String> getMembers() {
    return new 
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_37/left/TeamManager.java
    ArrayList
=======
    HashSet
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_37/right/TeamManager.java
    <>(members);
  }
}