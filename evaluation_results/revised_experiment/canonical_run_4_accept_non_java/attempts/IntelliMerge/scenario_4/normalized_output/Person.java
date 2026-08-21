public class Person {
    private int id;
    private String name;
    private String email;
<<<<<<< ours
    private Float phone
=======
    private int phone
>>>>>>> theirs
    ;
    
    public Person() {
    }
    
<<<<<<< ours
    public Person(int id, String name, String email, Float phone)
=======
    public Person(int id, String name, String email, int phone)
>>>>>>> theirs
     {
        this.id = id;
        this.name = name;
        this.email = email;
        this.phone = phone;
    }
    
    public int getId() {
        return id;
    }
    
    public void setId(int id) {
        this.id = id;
    }
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getEmail() {
        return email;
    }
    
    public void setEmail(String email) {
        this.email = email;
    }
    
<<<<<<< ours
    public Float getPhone()
=======
    public int getPhone()
>>>>>>> theirs
     {
        return phone;
    }
    
<<<<<<< ours
    public void setPhone(Float phone)
=======
    public void setPhone(int phone)
>>>>>>> theirs
     {
        this.phone = phone;
    }
    
    @Override
    public String toString() {
        return "Person{id=" + id + ", name='" + name + "'}";
    }
}