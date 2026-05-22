public class TeamManager {
    private Set<String> members = new HashSet<>();
    
    public void addMember(String member) {
        if (members.contains(member)) {
            throw new IllegalArgumentException("Member already exists");
        }
        members.add(member);
    }
    
    public Set<String> getMembers() {
        return new HashSet<>(members);
    }
}