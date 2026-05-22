public class TeamManager {
    private List<String> members = new ArrayList<>();
    
    public void addMember(String member) {
        members.add(member);
    }
    
    public List<String> getMembers() {
        return new ArrayList<>(members);
    }
}