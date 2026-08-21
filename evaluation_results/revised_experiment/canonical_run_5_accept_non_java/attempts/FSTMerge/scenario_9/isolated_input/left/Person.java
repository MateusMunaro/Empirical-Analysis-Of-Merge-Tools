public class Person {
    private int id;
    
    public Person() {
    }
    
    public Person(int id) {
        this.id = id;
    }
    
    public int getId() {
        return id;
    }
    
    public void setId(int id) {
        this.id = id;
    }
    
    
    @Override
    public String toString() {
        return "Person{id=" + id + "}";
    }
}