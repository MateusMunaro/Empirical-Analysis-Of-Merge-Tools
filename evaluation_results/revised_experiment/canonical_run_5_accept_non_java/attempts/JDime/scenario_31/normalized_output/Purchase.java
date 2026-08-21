public class Purchase {
    private int id;
    private double value;
    private List<Item> items;

    public Purchase(int id, double value, List<Item> items) {
        this.id = id;
        this.value = value;
        this.items = items;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public double getValue() {
        return value;
    }

    public void setValue(double value) {
        this.value = value;
    }

    public List<Item> getItems() {
        return items;
    }

    public void setItems(List<Item> items) {
        this.items = items;
    }
}