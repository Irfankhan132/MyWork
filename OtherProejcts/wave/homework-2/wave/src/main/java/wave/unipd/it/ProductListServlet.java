package wave.unipd.it;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Servlet implementation class ProductListServlet
 */
@WebServlet("/ProductList")
public class ProductListServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;


	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest req, HttpServletResponse res) throws ServletException, IOException {
		
		res.setContentType("text/html");
		PrintWriter pw = res.getWriter();
		
		RequestDispatcher dispatcher = null;
		
		Connection con = null;
		
		try {
			
			Class.forName("org.postgresql.Driver");
			con = DriverManager.getConnection("jdbc:postgresql://localhost:5432/wave","postgres","Hacker082@");
			PreparedStatement pst = con.prepareStatement("SELECT p_id, p_name, p_price, p_categries, "
					+ "p_size, p_quantity, p_description FROM products");
			
			ResultSet rs = pst.executeQuery();
			pw.println("<table border = '1' align = 'center'>");
			pw.println("<tr>");
			pw.println("<th>p_id</th>");
			pw.println("<th>p_name</th>");
			pw.println("<th>p_price</th>");
			pw.println("<th>p_categries</th>");
			pw.println("<th>p_size</th>");
			pw.println("<th>p_quantity</th>");
			pw.println("<th>p_description</th>");
			pw.println("<th>Edit</th>");
			pw.println("<th>Delete</th>");
			pw.println("</tr>");
			while(rs.next()) {					
				pw.println("<tr>");
				pw.println("<td>"+ rs.getString(1) +"</td>");
				pw.println("<td>"+ rs.getString(2) +"</td>");
				pw.println("<td>"+ rs.getInt(3) +"</td>");
				pw.println("<td>"+ rs.getString(4) +"</td>");
				pw.println("<td>"+ rs.getInt(5) +"</td>");
				pw.println("<td>"+ rs.getInt(6) +"</td>");
				pw.println("<td>"+ rs.getString(7) +"</td>");
				pw.println("<td><a href = 'editProduct?p_id=" + rs.getString(1) +"'>Edit</a></td>");
				pw.println("<td><a href = 'deleteProduct?p_id=" + rs.getString(1) +"'>Delete</a></td>");
				pw.println("</tr>");
			}
			pw.println("</table>");
		} catch (Exception e) {
			e.printStackTrace();
		}finally {
			try {
				
				if(con != null) {
					con.close();
					System.out.println("Connected from the PostgreSQL database.");
				}
				
			} catch (Exception e2) {
				// TODO: handle exception
				e2.printStackTrace();
			}
		}
		
		pw.println("<a href = 'index.jsp'> Home Page</a>");
		pw.println("<br>");
		pw.println("<a href = 'AddProduct.jsp'> Add Products</a>");
		
		
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest req, HttpServletResponse res) throws ServletException, IOException {
		// TODO Auto-generated method stub
		doGet(req, res);
	}

}
