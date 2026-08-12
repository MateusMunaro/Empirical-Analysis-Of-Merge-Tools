public class Purchase {
    private int id;
    private double value;
    private List<Item> items;
    private Date orderDate;

    public Purchase(int id, double value, List<Item> items, Date orderDate) {
        this.id = id;
        this.value = value;
        this.items = items;
        this.orderDate = orderDate;
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

    public Date getOrderDate() {
        return orderDate;
    }

    public void setOrderDate(Date orderDate) {
        this.orderDate = orderDate;
    }
}
