export default function ErrorState({ message }) {
  return (
    <section className="empty-state error-state">
      <h2>Não foi possível carregar</h2>
      <p>{message}</p>
    </section>
  );
}
