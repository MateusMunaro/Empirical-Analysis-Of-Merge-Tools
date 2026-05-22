public   class  Profile {
	
    private String bio  ;

	

    public Profile(String bio) {
        this.bio = bio;
    }

	

    public String getBio  () {
        return bio;
    }

	

    public void setBio  (String bio) {
        this.bio = bio;
    }

	
    private Date joinDate;

	 

    public Profile(String bio, Date joinDate) {
        this.bio = bio;
        this.joinDate = joinDate;
    }

	

    public Date getJoinDate() {
        return joinDate;
    }

	

    public void setJoinDate(Date joinDate) {
        this.joinDate = joinDate;
    }


}
