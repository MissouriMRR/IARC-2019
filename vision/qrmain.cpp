#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <vector>

#include <GL/glew.h>
#include <GLFW/glfw3.h>
#include <glm/glm.hpp>
using namespace glm;

#include <opencv2/opencv.hpp>

#include "shader_loader.h"

void GLAPIENTRY MessageCallback(GLenum source, GLenum type, GLuint id, GLenum severity, GLsizei length, const GLchar* message, const void* userParam ){fprintf( stderr, "GL CALLBACK: %s type = 0x%x, severity = 0x%x, message = %s\n", ( type == GL_DEBUG_TYPE_ERROR ? "** GL ERROR **" : "" ), type, severity, message );}
static void glfwError(int id, const char* description){std::cout << description << std::endl;}

const int INT_PER_VERTEX = 3;


class TSSpace{
  public:
		GLFWwindow* window;

		const char* vshader = "shaders/vertex.glsl";
		const char* fshader = "shaders/fragment_accumulator.glsl";

		// Width in fragment_accumulator as magic number
		int WIDTH = 1024, HEIGHT = 768; 

		GLuint BUFF_SIZE = WIDTH * HEIGHT;
		GLsizeiptr BUFF_DATA_SIZE = BUFF_SIZE * sizeof(GLuint);

		GLuint tex, buf;

		GLuint image_unit = 0;

		GLuint VCOUNT, VSIZE;
		GLsizeiptr VERTEX_DATA_SIZE;
  		GLfloat *g_vertex_buffer_data = nullptr;

  	TSSpace(){
		/* 
		@fn TSSpace
		@breif Setup opengl.
		*/
		setup_opengl();
	}

	TSSpace(const GLuint vertex_count, GLfloat *vertex_values){
		/* 
		@fn TSSpace
		@breif Setup opengl and set verticies.

		@param vertex_count uint Number of 3D verticies in 
				vertex_values.
		@param vertex_values Glfloat* XYZ locations of verticies, 
				every 2 values is a line.
		*/
		setup_opengl();

		set_verticies(vertex_count , vertex_values);
	}

	void setup_opengl(){
		/*
		@fn setup_opengl
		@breif Do all of the opengl window setup.
		*/
		glEnable( GL_DEBUG_OUTPUT );
		glfwSetErrorCallback(&glfwError);

		glewExperimental = true; // Needed for core profile
		if(!glfwInit()){
			fprintf( stderr, "Failed to initialize GLFW\n" );
			throw std::runtime_error("Failed to initialize GLFW.");
		}
	
		glfwWindowHint(GLFW_SAMPLES, 1); // antialiasing
		glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4); // 4.3
		glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
		glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
		glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

		window = glfwCreateWindow(WIDTH, HEIGHT, "TS Space", NULL, NULL);
		if(window == NULL){
			glfwTerminate();

			fprintf(stderr, "Failed to open GLFW window.\n");
			throw std::runtime_error("Failed to open GLFW window.");
		}
		glfwMakeContextCurrent(window); 
		
		glewExperimental=true;
		if (glewInit() != GLEW_OK){
			fprintf(stderr, "Failed to initialize GLEW\n");
			throw std::runtime_error("Failed to initialize GLEW");
		}

		glEnable              (GL_DEBUG_OUTPUT);
		glDebugMessageCallback(MessageCallback, 0);
	}

	void set_verticies(const GLuint vertex_count, GLfloat *vertex_values){
		/* 
		@fn set_verticies
		@breif Sets space verticies to create lines.

		@param vertex_count uint Number of 3D verticies in 
				vertex_values.
		@param vertex_values Glfloat* XYZ locations of verticies, 
				every 2 values is a line.
		*/
		VCOUNT = vertex_count;
		VSIZE = VCOUNT * INT_PER_VERTEX;
		VERTEX_DATA_SIZE = VSIZE * sizeof(GLfloat);

		g_vertex_buffer_data = new GLfloat[VSIZE];
		g_vertex_buffer_data = vertex_values;
	}

	void accumulate(){
		/* 
		@fn accumulate
		@breif Counts number of lines drawn on each pixel.

		@pre Opengl is initialized, verticies are set and shaders exist.
		*/

		// setup
		GLuint filler[BUFF_SIZE] = {0};

		glGenBuffers(1, &buf);
		glBindBuffer(GL_TEXTURE_BUFFER, buf);
		glBufferData(GL_TEXTURE_BUFFER, BUFF_DATA_SIZE, filler, 
			GL_DYNAMIC_COPY);

		glGenTextures(1, &tex);

		glBindTexture(GL_TEXTURE_BUFFER, tex); 
		glTexBuffer(GL_TEXTURE_BUFFER, GL_R32UI, buf);

		glBindImageTexture(image_unit, tex, 0, GL_FALSE, 0, 
			GL_READ_WRITE, GL_R32UI); 

		GLuint VertexArrayID;
		glGenVertexArrays(1, &VertexArrayID);
		glBindVertexArray(VertexArrayID);
		
		GLuint vertexbuffer;  
		glGenBuffers(1, &vertexbuffer);
		glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer);  
		glBufferData(GL_ARRAY_BUFFER, VERTEX_DATA_SIZE, 
			g_vertex_buffer_data, GL_STATIC_DRAW);

		GLuint programID = LoadShaders(vshader, fshader); 

		//glOrtho(0, WIDTH, HEIGHT, 0, 0, 1);

		// process
		//do {
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
		glClearColor(0.0f, 0.0f, 0.0f, 0.0f) ;

		glEnableVertexAttribArray(0);
		glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer);

		glVertexAttribPointer(0, INT_PER_VERTEX, GL_FLOAT, GL_FALSE, 
			0, (void*)0);

 		glUseProgram(programID);
		
		glDrawArrays(GL_LINES, 0, VCOUNT);

		glDisableVertexAttribArray(0);
	
		glfwSwapBuffers(window);
		
		// DEBUG
		glfwPollEvents();
		//}while( glfwGetKey(window, GLFW_KEY_ESCAPE ) != GLFW_PRESS && glfwWindowShouldClose(window) == 0 );
	}
	
	cv::Mat convert_output(){
		/* 
		@fn convert_output
		@breif Convert processed data into opencv mat.

		@pre Buffer id buf contains processed values.

		@return Opencv mat[HEIGHT][WIDTH]
		*/
	
		// buffer -> vector
		GLuint *initial = new GLuint[BUFF_SIZE];
		glGetNamedBufferSubData(buf, 0, BUFF_DATA_SIZE, initial);

		glfwDestroyWindow(window);  // cannot destroy window before read


		// DEBUG
		std::map<GLuint, uint> instance_counter;
		for (uint x = 0; x < BUFF_SIZE; x++){
			GLuint value = initial[x];

			if(instance_counter.find(value) == instance_counter.end())
				instance_counter.insert(
					std::pair<GLuint, uint>(value, 0));

			instance_counter[value] += 1;
		}
		for(auto elem : instance_counter)
		  std::cout << elem.first << " " << elem.second << std::endl;


		// vector -> mat
		// CV_16UC1 = ushort, [0, 65535]
		cv::Mat intermediate(HEIGHT, WIDTH, CV_16UC1, cv::Scalar(0));  
		for (int i = 0; i < HEIGHT; i++){
			for (int j = 0; j < WIDTH; j++){
				intermediate.at<ushort>(HEIGHT - i - 1, j) = initial[(i*WIDTH) + j];
			}
		}
		
		cv::Mat finish;
		cv::normalize(intermediate, finish, 0, 65535, cv::NORM_MINMAX);

    	return finish;
	}
};


int main(){
  const GLuint VCOUNT = 10;

  // 0, 0 is in the middle of opengl, 1,1 is top right

  GLfloat verticies[VCOUNT*INT_PER_VERTEX] = {
		-1.0f, -1.0f, 0.0f,
		1.0f, 1.0f, 0.0f,
		-1.0f,  1.0f, 0.0f,
		1.0f, -1.0f, 0.0f,
		-1.0f, 0.5f, 0.0f,
		1.0f,  0.5f, 0.0f,

		0.0f, 1.0f, 0.0f,
		0.0f, -1.0f, 0.0f,
		0.0f, 1.0f, 0.0f,
		0.0f, -1.0f, 0.0f,
		};

  TSSpace tsspace(VCOUNT , verticies);

  tsspace.accumulate(); 

  cv::Mat output = tsspace.convert_output();

  cv::imshow("Accumulated values", output);
  cv::waitKey(0);

  // note: mat is upsidown from opengl, flipped horizontally?

  return 0;
}
