public class Person {
    private int id;
    private String phone;
    
<<<<<<< ours
    public Person(int id, String email, String phone)
=======
    public Person(int id, String name, String phone)
>>>>>>> theirs
     {
        this.id = id;
<<<<<<< ours
        this.email = email;
=======
        this.name = name;
>>>>>>> theirs
        this.phone = phone;
    }
    
    public int getId() {
        return id;
    }
    
    public void setId(int id) {
        this.id = id;
    }
    
    public String getPhone() {
        return phone;
    }
    
    public void setPhone(String phone) {
        this.phone = phone;
    }
    
}