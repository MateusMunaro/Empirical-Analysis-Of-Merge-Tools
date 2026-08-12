public   class  User {
	
    private int id  ;

	
    private String username  ;

	

    public User(int id, String username) {
        this.id = id;
        this.username = username;
    }

	

    public int getId  () {
        return id;
    }

	

    public void setId  (int id) {
        this.id = id;
    }

	

    public String getUsername  () {
        return username;
    }

	

    public void setUsername  (String username) {
        this.username = username;
    }

	
    private String email;

	 

    public User(int id, String username, String email) {
        this.id = id;
        this.username = username;
        this.email = email;
    }

	

    public String getEmail() {
        return email;
    }

	

    public void setEmail(String email) {
        this.email = email;
    }


}
