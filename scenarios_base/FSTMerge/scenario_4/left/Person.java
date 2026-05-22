public class Person {
    private int id;
    private String name;
    private String email;
    private Float phone;
    
    public Person() {
    }
    
    public Person(int id, String name, String email, Float phone) {
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
    
    public Float getPhone() {
        return phone;
    }
    
    public void setPhone(Float phone) {
        this.phone = phone;
    }
    
    @Override
    public String toString() {
        return "Person{id=" + id + ", name='" + name + "'}";
    }
}