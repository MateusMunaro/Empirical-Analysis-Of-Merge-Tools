public class Client {
    private int clientId;
    private String name;
    private Address address;

    public Client(int clientId, String name, Address address) {
        this.clientId = clientId;
        this.name = name;
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

    public Address getAddress() {
        return address;
    }

    public void setAddress(Address address) {
        this.address = address;
    }
}



