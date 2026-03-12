public class Person {
    private int id;
    private String name;
    private String email;
    private int phone;
    
    public Person() {
    }
    
    public Person(int id, String name, String email, int phone) {
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
    
    public int getPhone() {
        return phone;
    }
    
    public void setPhone(int phone) {
        this.phone = phone;
    }
    
    @Override
    public String toString() {
        return "Person{id=" + id + ", name='" + name + "'}";
    }
}