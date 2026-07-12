import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <section>
      <h1>Page Not Found</h1>
      <p>The requested route does not exist.</p>
      <p>
        <Link to="/analyse">Go to analysis</Link>
      </p>
    </section>
  );
}
