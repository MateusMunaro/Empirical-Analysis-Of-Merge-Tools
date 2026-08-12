public class NotificationService {
    private Map<String, NotificationStrategy> strategies;
    
    public NotificationService() {
        strategies = new HashMap<>();
        strategies.put("EMAIL", new EmailStrategy());
        strategies.put("SMS", new SmsStrategy());
        strategies.put("PUSH", new PushStrategy());
    }
    
    public void sendNotification(String message, String recipient, String type) {
        NotificationStrategy strategy = strategies.get(type);
        if (strategy != null) {
            strategy.send(message, recipient);
        }
    }
}