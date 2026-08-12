public  class  PaymentValidator {
	
    private static final List<String> VALID_PAYMENT_METHODS = Arrays.asList(
        "CREDIT_CARD", "DEBIT_CARD", "PIX", "BOLETO"
    );

	
    
    public void validate(String paymentMethod) {
        if (paymentMethod == null || paymentMethod.trim().isEmpty()) {
            throw new ValidationException("Método de pagamento é obrigatório");
        }
        
        if (!VALID_PAYMENT_METHODS.contains(paymentMethod)) {
            throw new ValidationException("Método de pagamento inválido: " + paymentMethod);
        }
        
        // Validações específicas por método
        validatePaymentMethodSpecifics(paymentMethod);
    }

	
    
    private void validatePaymentMethodSpecifics(String paymentMethod) {
        switch (paymentMethod) {
            case "BOLETO":
                // Boleto tem limitações de horário
                Calendar cal = Calendar.getInstance();
                int hour = cal.get(Calendar.HOUR_OF_DAY);
                if (hour < 6 || hour > 22) {
                    throw new ValidationException("Boleto só pode ser gerado entre 6h e 22h");
                }
                break;
                
            case "PIX":
                // PIX tem limite diário
                // Esta validação seria mais complexa na prática
                break;
        }
    }


}
