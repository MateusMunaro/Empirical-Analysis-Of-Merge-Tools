public class TeamManager {
<<<<<<< ours
    private List<String> members
=======
    private Set<String> members
>>>>>>> theirs
<<<<<<< ours
     = new ArrayList<>();
=======
     = new HashSet<>();
>>>>>>> theirs
    
    
    public void addMember(String member) {
<<<<<<< ours
=======
        if (members.contains(member)) {
            throw new IllegalArgumentException("Member already exists");
        }
>>>>>>> theirs
        members.add(member);
    }
    
    public List<String> getMembers() {
        return new ArrayList<>(members);
    }
    public Set<String> getMembers() {
        return new HashSet<>(members);
    }
}