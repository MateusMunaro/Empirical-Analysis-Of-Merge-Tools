public   class  Person {
	
    private int id  ;

	
    private String name;

	
    private String email  ;

	
    private String phone  ;

	
    
    public Person() {
    }

	
    
    public Person(int id, String name) {
        this.id = id;
        this.name = name;
    }

	

    public int getId  () {
        return id;
    }

	

    public void setId  (int id) {
        this.id = id;
    }

	
    
    public String getName() {
        return name;
    }

	
    
    public void setName(String name) {
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

	
    
    @Override
    public String toString() {
        return "Person{id=" + id + ", name='" + name + "'}";
    }

	
    private String fullName;

	

    public Person(int id, String fullName, String email, String phone) {
        this.id = id;
        this.fullName = fullName;
        this.email = email;
        this.phone = phone;
    }

	
    
    public String getFullName() {
        return fullName;
    }

	
    
    public void setFullName(String fullName) {
        this.fullName = fullName;
    }


}
