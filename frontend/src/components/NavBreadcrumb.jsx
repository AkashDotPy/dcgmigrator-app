// Breadcrumb.jsx
import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Breadcrumb = () => {
    const location = useLocation();
    const pathnames = location.pathname.split('/').filter((x) => x);

    return (
        <nav className="mb-10 w-full" aria-label="breadcrumb">
            <ol className="list-reset flex">
                <li className="text-gray-500">
                    <Link to="/" className="text-blue-600 hover:text-blue-700">Home</Link>
                </li>
                {pathnames.map((value, index) => {
                    const to = `/${pathnames.slice(0, index + 1).join('/')}`;
                    const isLast = index === pathnames.length - 1;

                    return isLast ? (
                        <li key={to} className="text-gray-500 mx-2">
                            <span className="mx-2">/</span>
                            <span>{value}</span>
                        </li>
                    ) : (
                        <li key={to} className="text-gray-500 mx-2">
                            <span className="mx-2">/</span>
                            <Link to={to} className="text-blue-600 hover:text-blue-700">{value}</Link>
                        </li>
                    );
                })}
            </ol>
        </nav>
    );
};

export default Breadcrumb;
