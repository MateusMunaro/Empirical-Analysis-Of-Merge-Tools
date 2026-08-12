public  class  UserContact {
	
    private String email;

	
    private String phone;

	

    public UserContact(String email, String phone) {
        this.email = email;
        this.phone = phone;
    }

	

    public String getEmail() {
        return email;
    }

	

    public String getPhone() {
        return phone;
    }

	

    public void setEmail(String email) {
        this.email = email;
    }

	

    public void setPhone(String phone) {
        this.phone = phone;
    }


}
