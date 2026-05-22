public class NotificationService {
    private Map<String, NotificationStrategy> strategies;
    private Logger logger = Logger.getLogger(NotificationService.class.getName());
    
    public NotificationService() {
        strategies = new HashMap<>();
        strategies.put("EMAIL", new EmailStrategy());
        strategies.put("SMS", new SmsStrategy());
        strategies.put("PUSH", new PushStrategy());
    }
    
    public void sendNotification(String message, String recipient, String type) {
        logger.info("Iniciando envio de notificação tipo: " + type);
        
        try {
            NotificationStrategy strategy = strategies.get(type);
            if (strategy != null) {
                strategy.send(message, recipient);
                logger.info("Notificação enviada com sucesso para: " + recipient);
            } else {
                logger.warning("Tipo de notificação não suportado: " + type);
            }
        } catch (Exception e) {
            logger.severe("Erro ao enviar notificação: " + e.getMessage());
            throw e;
        }
    }
}