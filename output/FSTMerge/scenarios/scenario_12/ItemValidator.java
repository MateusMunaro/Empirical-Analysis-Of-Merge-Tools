public  class  ItemValidator {
	
    public void validate(List<OrderItem> items) {
        if (items == null || items.isEmpty()) {
            throw new ValidationException("Pedido deve ter pelo menos um item");
        }
        
        if (items.size() > 100) {
            throw new ValidationException("Pedido não pode ter mais de 100 itens");
        }
        
        for (OrderItem item : items) {
            validateSingleItem(item);
        }
    }

	
    
    private void validateSingleItem(OrderItem item) {
        if (item.getQuantity() <= 0) {
            throw new ValidationException("Quantidade deve ser positiva");
        }
        
        if (item.getQuantity() > 1000) {
            throw new ValidationException("Quantidade não pode exceder 1000 unidades");
        }
        
        if (item.getPrice().compareTo(BigDecimal.ZERO) <= 0) {
            throw new ValidationException("Preço deve ser positivo");
        }
        
        if (item.getPrice().compareTo(new BigDecimal("100000")) > 0) {
            throw new ValidationException("Preço unitário não pode exceder R$ 100.000");
        }
    }


}
