public   class  Person {
	
    private int id  ;

	
    private String name  ;

	
    private String email  ;

	
    private String phone  ;

	
    private Date birthDate;

	
    
    public Person(int id, String name, String email, String phone, Date birthDate) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.phone = phone;
        this.birthDate = birthDate;
    }

	

    public int getId  () {
        return id;
    }

	
    
    public void setId  (int id) {
        this.id = id;
    }

	

    public String getName  () {
        return name;
    }

	

    public void setName  (String name) {
        this.name = name;
    }

	

    public String getEmail  () {
        return email;
    }

	

    public void setEmail  (String email) {
        this.email = email;
    }

	

    public String getPhone  () {
        return phone;
    }

	

    public void setPhone  (String phone) {
        this.phone = phone;
    }

	

    public Date getBirthDate() {
        return birthDate;
    }

	

    public void setBirthDate(Date birthDate) {
        this.birthDate = birthDate;
    }

	
    
    public Person(int id, String name, String email, String phone) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.phone = phone;
    }


}
