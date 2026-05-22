public  class  CustomerValidator {
	
    public void validate(Long customerId) {
        if (customerId == null || customerId <= 0) {
            throw new ValidationException("ID do cliente inválido");
        }
        
        // Validação adicional específica de cliente
        if (customerId > 999999) {
            throw new ValidationException("ID do cliente fora do range válido");
        }
    }


}
