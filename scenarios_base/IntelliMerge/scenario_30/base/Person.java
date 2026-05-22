public class Person {
    private int id;
    private String name;
    private String email;

    public Person(int id, String name) {
        this.id = id;
        this.name = name;
        this.email = null;
    }

    public int getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setId(int id) {
        this.id = id;
    }


}

