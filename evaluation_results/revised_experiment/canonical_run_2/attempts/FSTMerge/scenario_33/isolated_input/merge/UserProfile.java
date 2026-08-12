public  class  UserProfile {
	
    private String bio;

	
    private String location;

	

    public UserProfile(String bio, String location) {
        this.bio = bio;
        this.location = location;
    }

	

    public String getBio() {
        return bio;
    }

	

    public void setBio(String bio) {
        this.bio = bio;
    }

	

    public String getLocation() {
        return location;
    }

	

    public void setLocation(String location) {
        this.location = location;
    }


}
