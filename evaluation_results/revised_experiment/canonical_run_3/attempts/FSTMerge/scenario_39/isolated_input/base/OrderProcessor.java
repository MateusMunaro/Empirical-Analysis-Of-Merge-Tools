public class OrderProcessor {
    
    public double processCustomerOrder(Customer customer, Order order) {
        double discount = customer.calculateDiscount(order.getAmount());
        double total = order.calculateTotal() - discount;
        order.processOrder();
        return total;
    }
    
    public String getOrderSummary(Customer customer, Order order) {
        return "Order " + order.getOrderId() + " for customer " + customer.getName() + 
               " - Amount: $" + order.getAmount();
    }
}