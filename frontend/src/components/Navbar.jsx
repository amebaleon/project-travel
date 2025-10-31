import React from "react";
import "./Navbar.css";
import "bootstrap/dist/css/bootstrap.min.css";

export default function Navbar() {
  return (
    <nav className="navbar-container d-flex align-items-center justify-content-between px-5">
      <div className="navbar-logo">
        <h1 className="navbar-logo">Tour ai</h1>
      </div>
      <ul className="navbar-menu d-flex mb-0">
        <li>
          <a href="#">Home</a>
        </li>
        <li>
          <a href="#">About Us</a>
        </li>
      </ul>
    </nav>
  );
}
