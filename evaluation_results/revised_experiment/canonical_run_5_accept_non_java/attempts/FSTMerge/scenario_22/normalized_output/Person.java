public   class  Person {
	
    private int id  ;

	
    
    public Person(int id) {
        this.id = id;
    }

	

    public int getId  () {
        return id;
    }

	

    public void setId  (int id) {
        this.id = id;
    }

	
    private String name;

	
    private String nationality;

	 
    
    public Person(int id, String name, String nationality) {
        this.id = id;
        this.name = name;
        this.nationality = nationality;
    }

	

    public String getName() {
        return name;
    }

	

    public void setName(String name) {
        this.name = name;
    }

	

    public String getNationality() {
        return nationality;
    }

	

    public void setNationality(String nationality) {
        this.nationality = nationality;
    }


}
