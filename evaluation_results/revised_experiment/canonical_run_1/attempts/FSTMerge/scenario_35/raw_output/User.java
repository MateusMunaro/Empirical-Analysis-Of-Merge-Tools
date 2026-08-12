public   class  User {
	
    private String username  ;

	
    private int age  ;

	
    
    public void setAge  (int age) {
        if (age < 18 || age > 150) {
            throw new IllegalArgumentException("Age must be between 18 and 150");
        }
        this.age = age;
    }


}
