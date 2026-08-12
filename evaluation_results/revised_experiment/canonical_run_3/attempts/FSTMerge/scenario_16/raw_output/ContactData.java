public  class  ContactData {
	
    private String email;

	
    private PhoneNumber phone;

	 
    
    public  class  PhoneNumber {
		
        private String countryCode;

		
        private String number;


	}

	

    public ContactData(String email, PhoneNumber phone) {
        this.email = email;
        this.phone = phone;
    }

	

    public String getEmail() {
        return email;
    }

	

    public void setEmail(String email) {
        this.email = email;
    }

	

    public PhoneNumber getPhone() {
        return phone;
    }

	

    public void setPhone(PhoneNumber phone) {
        this.phone = phone;
    }


}
