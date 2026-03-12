import java.util.*;

public class TeamManager {
    private Set<String> members = new LinkedHashSet<>();
    
    public void addMember(String member) {
        if (members.contains(member)) {
            throw new IllegalArgumentException("Member already exists");
        }
        members.add(member);
    }
    
    public List<String> getMembers() {
        return new ArrayList<>(members);
    }
    
    public Set<String> getMembersAsSet() {
        return new LinkedHashSet<>(members);
    }
}