# EAP to Quarkus examples

This readme contains examples of code changes needed to migrate an EAP app to Quarkus

## Source and Target Technologies

Source Tech:
* EAP 7
* Java 8

Target tech:
* Quarkus 3.4.1
* Java 11

Source code: https://github.com/savitharaghunathan/kitchensink/compare/main...quarkus

## Code changes:

### Database config

1. **DB configuration** :

In Quarkus, Hibernate ORM can be configured without the need for a persistence.xml resource. While it's an option for advanced configurations, it's often unnecessary.

Application Properties:

All configuration settings for Hibernate ORM can be added to your application.properties file. This is where the database connection details, such as the database URL, username, and password, are specified.

eg:
* [EAP - Remove persistence.xml](https://github.com/savitharaghunathan/kitchensink/compare/main...quarkus#diff-5519d2b0765548d40a1806f7a0acf6db8f8205065f51e0d696eea2edd111c26cL1)

* [Quarkus - Configure application.prperties](https://github.com/savitharaghunathan/kitchensink/blob/e0391746f3c05e39c45cd0a06dc35beab1e6a365/src/main/resources/application.properties)

2. **Transaction Handling**:

Mark the CDI bean method as @Transactional and the EntityManager will enlist and flush at commit.

eg:

* [EAP](https://github.com/savitharaghunathan/kitchensink/compare/main...quarkus#diff-03a229fb3ab55d31c4c88d8ad0979aa41e2aa1c83c9abebfde58a1ee274974b1L40)
* [Quarkus](https://github.com/savitharaghunathan/kitchensink/compare/main...quarkus#diff-03a229fb3ab55d31c4c88d8ad0979aa41e2aa1c83c9abebfde58a1ee274974b1R42)


### Scope changes

1. In Quarkus, the @Stateless bean scope is not a built-in scope. it follows a different approach to bean scopes, and the equivalent of a stateless bean is implemented using other CDI (Contexts and Dependency Injection) scopes, such as @RequestScoped, @ApplicationScoped, or @Dependent. 

@ApplicationScoped is most common used replacement for @Stateless scope

eg: 
* [EAP](https://github.com/savitharaghunathan/kitchensink/compare/main...quarkus#diff-03a229fb3ab55d31c4c88d8ad0979aa41e2aa1c83c9abebfde58a1ee274974b1L28) 
* [Quarkus](https://github.com/savitharaghunathan/kitchensink/compare/main...quarkus#diff-03a229fb3ab55d31c4c88d8ad0979aa41e2aa1c83c9abebfde58a1ee274974b1R30)

### Dependency changes
Quarkus-specific dependencies 

1. **Database Dependency Changes**:


```
<!-- Hibernate ORM specific dependencies -->
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-hibernate-orm</artifactId>
</dependency>

<!-- JDBC driver dependencies -->
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-jdbc-postgresql</artifactId>
</dependency>

<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-hibernate-validator</artifactId>
</dependency>
```

2. **JSF Integration**:

```
<dependency>
    <groupId>org.apache.myfaces.core.extensions.quarkus</groupId>
    <artifactId>myfaces-quarkus</artifactId>
    <version>4.0.1</version>
</dependency>
```

3. **Quarkus Application Runtime Container** (access to the core functionality required for dependency injection, context management, and bean management) 

```
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-arc</artifactId>
</dependency>
```

4. **REST**

```
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-resteasy-reactive</artifactId>
</dependency>
```

5. **Testing**

```
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-junit5</artifactId>
    <scope>test</scope>
</dependency>

<!-- \Testing RESTful web services -->
<dependency>
    <groupId>io.rest-assured</groupId>
    <artifactId>rest-assured</artifactId>
    <scope>test</scope>
</dependency>
```
