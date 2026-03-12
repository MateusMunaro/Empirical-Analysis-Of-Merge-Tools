
public class TeamManager {
  private 
<<<<<<< ./senarios_merge_base/JDime/scenario_37/left/teamManager.java
  List
=======
  Set
>>>>>>> ./senarios_merge_base/JDime/scenario_37/right/teamManager.java
  <String> members = new 
<<<<<<< ./senarios_merge_base/JDime/scenario_37/left/teamManager.java
  ArrayList
=======
  HashSet
>>>>>>> ./senarios_merge_base/JDime/scenario_37/right/teamManager.java
  <>();

  public void addMember(String member) {

<<<<<<< Unknown file: This is a bug in JDime.
=======
    if (members.contains(member)) {
      throw new IllegalArgumentException("Member already exists");
    }
>>>>>>> ./senarios_merge_base/JDime/scenario_37/right/teamManager.java

    members.add(member);
  }

  public 
<<<<<<< ./senarios_merge_base/JDime/scenario_37/left/teamManager.java
  List
=======
  Set
>>>>>>> ./senarios_merge_base/JDime/scenario_37/right/teamManager.java
  <String> getMembers() {
    return new 
<<<<<<< ./senarios_merge_base/JDime/scenario_37/left/teamManager.java
    ArrayList
=======
    HashSet
>>>>>>> ./senarios_merge_base/JDime/scenario_37/right/teamManager.java
    <>(members);
  }
}