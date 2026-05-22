public class TeamManager {
    private String[] members;
    
    public void addMember(String member) {
        if (members == null) {
            members = new String[0];
        }
        for (String m : members) {
            if (m.equals(member)) {
                throw new IllegalArgumentException("Member already exists");
            }
        }
        String[] newMembers = new String[members.length + 1];
        System.arraycopy(members, 0, newMembers, 0, members.length);
        newMembers[members.length] = member;
        members = newMembers;
    }
}