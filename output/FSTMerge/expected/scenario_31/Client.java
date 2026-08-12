public class Client {
    private int clientId;
    private String name;
    private String email;
    private Address address;

    public Client(int clientId, String name, String email, Address address) {
        this.clientId = clientId;
        this.name = name;
        this.email = email;
        this.address = address;
    }

    public int getClientId() {
        return clientId;
    }

    public void setClientId(int clientId) {
        this.clientId = clientId;
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

    public Address getAddress() {
        return address;
    }

    public void setAddress(Address address) {
        this.address = address;
    }
}



