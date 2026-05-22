public class ShippingValidator {
    private static final List<String> VALID_REGIONS = Arrays.asList(
        "SP", "RJ", "MG", "RS", "PR", "SC", "BA", "GO", "PE", "CE"
    );
    
    public void validate(String shippingAddress) {
        if (shippingAddress == null || shippingAddress.trim().isEmpty()) {
            throw new ValidationException("Endereço de entrega é obrigatório");
        }
        
        if (shippingAddress.length() < 10) {
            throw new ValidationException("Endereço deve ter pelo menos 10 caracteres");
        }
        
        if (shippingAddress.length() > 200) {
            throw new ValidationException("Endereço não pode exceder 200 caracteres");
        }
        
        // Validação de região (simplificada)
        boolean validRegion = VALID_REGIONS.stream()
            .anyMatch(region -> shippingAddress.toUpperCase().contains(region));
        
        if (!validRegion) {
            throw new ValidationException("Região de entrega não atendida");
        }
    }
}